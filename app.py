import openai
import boto3
import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from mock_rds_data import get_mock_rds_data

VALID_FIELDS = [
    'DBInstanceIdentifier', 'DBInstanceClass', 'Engine', 'DBInstanceStatus', 'MasterUsername', 'Endpoint',
    'AllocatedStorage', 'InstanceCreateTime', 'PreferredBackupWindow', 'BackupRetentionPeriod', 'DBSecurityGroups',
    'VpcSecurityGroups', 'DBParameterGroups', 'AvailabilityZone', 'DBSubnetGroup', 'PreferredMaintenanceWindow',
    'PendingModifiedValues', 'LatestRestorableTime', 'MultiAZ', 'EngineVersion', 'AutoMinorVersionUpgrade',
    'ReadReplicaDBInstanceIdentifiers', 'LicenseModel', 'OptionGroupMemberships', 'PubliclyAccessible', 'StorageType',
    'DbInstancePort', 'StorageEncrypted', 'KmsKeyId', 'DbiResourceId', 'CACertificateIdentifier', 'DomainMemberships',
    'CopyTagsToSnapshot', 'MonitoringInterval', 'DBInstanceArn', 'IAMDatabaseAuthenticationEnabled', 'DatabaseInsightsMode',
    'PerformanceInsightsEnabled', 'DeletionProtection', 'AssociatedRoles', 'MaxAllocatedStorage', 'TagList',
    'CustomerOwnedIpEnabled', 'ActivityStreamStatus', 'BackupTarget', 'NetworkType', 'StorageThroughput',
    'CertificateDetails', 'DedicatedLogVolume', 'IsStorageConfigUpgradeAvailable', 'EngineLifecycleSupport'
]

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")

# Global variable to hold cached RDS data
cached_rds_data = []

last_refresh_time = 0  # store as UNIX timestamp
REFRESH_INTERVAL = 5 * 60  # 5 minutes in seconds
using_mock_data = False  # Track if we're using mock data
rds_client = None  # Global RDS client


# Initialize FastAPI
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")

# OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    # Always reset chat history on refresh
    request.session["messages"] = []

    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "chat_history": []}
    )

# Define function to fetch RDS fields
def fetch_rds_fields(queries):
    selected_fields = []
    for query in queries:
        instance = query["instance"]
        field = query["field"]

        db_data = next((db for db in cached_rds_data if db['DBInstanceIdentifier'] == instance), None)

        if not db_data:
            selected_fields.append({
                "instance": instance,
                "field": field,
                "value": "Instance not found"
            })
            continue

        if field not in VALID_FIELDS:
            value = "Field not available"
        else:
            value = db_data.get(field, "Not Found")
            if isinstance(value, datetime):
                value = value.isoformat()

        selected_fields.append({
            "instance": instance,
            "field": field,
            "value": value
        })

    return selected_fields

# Define functions for OpenAI
functions = [
    {
        "name": "fetch_rds_fields",
        "description": (
            "Fetch specific fields from specific RDS instances. "
            "Each query must provide a database instance identifier and a field name. "
            "Valid field names are: DBInstanceIdentifier, DBInstanceClass, Engine, DBInstanceStatus, MasterUsername, Endpoint, "
            "AllocatedStorage, InstanceCreateTime, PreferredBackupWindow, BackupRetentionPeriod, DBSecurityGroups, VpcSecurityGroups, "
            "DBParameterGroups, AvailabilityZone, DBSubnetGroup, PreferredMaintenanceWindow, PendingModifiedValues, "
            "LatestRestorableTime, MultiAZ, EngineVersion, AutoMinorVersionUpgrade, ReadReplicaDBInstanceIdentifiers, "
            "LicenseModel, OptionGroupMemberships, PubliclyAccessible, StorageType, DbInstancePort, StorageEncrypted, "
            "KmsKeyId, DbiResourceId, CACertificateIdentifier, DomainMemberships, CopyTagsToSnapshot, MonitoringInterval, "
            "DBInstanceArn, IAMDatabaseAuthenticationEnabled, DatabaseInsightsMode, PerformanceInsightsEnabled, DeletionProtection, "
            "AssociatedRoles, MaxAllocatedStorage, TagList, CustomerOwnedIpEnabled, ActivityStreamStatus, BackupTarget, NetworkType, "
            "StorageThroughput, CertificateDetails, DedicatedLogVolume, IsStorageConfigUpgradeAvailable, EngineLifecycleSupport."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "description": "A list of (instance, field) pairs to retrieve.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "instance": {
                                "type": "string",
                                "description": "The DBInstanceIdentifier of the RDS instance."
                            },
                            "field": {
                                "type": "string",
                                "description": "The field name to retrieve. Must match one of the valid field names listed in the description."
                            }
                        },
                        "required": ["instance", "field"]
                    }
                }
            },
            "required": ["queries"]
        }
    }
]

@app.post("/chat")
async def post_chat(request: Request, user_message: str = Form(...)):
    global cached_rds_data, last_refresh_time, using_mock_data, rds_client

    # Save user message into session
    request.session["messages"].append({"role": "user", "content": user_message})

    # Refresh RDS data if needed
    if not using_mock_data:
        current_time = time.time()
        if current_time - last_refresh_time > REFRESH_INTERVAL:
            try:
                response = rds_client.describe_db_instances()
                cached_rds_data = response['DBInstances']
                last_refresh_time = current_time
                print("✅ Refreshed RDS data from AWS.")
            except Exception as e:
                print(f"❌ Failed to refresh RDS data: {e}")

    # Memory limit: Keep only the last 40 messages (user + assistant)
    MAX_MEMORY_MESSAGES = 40
    if len(request.session["messages"]) > MAX_MEMORY_MESSAGES:
        request.session["messages"] = request.session["messages"][-MAX_MEMORY_MESSAGES:]

    # Build dynamic system prompt
    instance_names = [db['DBInstanceIdentifier'] for db in cached_rds_data]
    instance_list_str = ", ".join(instance_names)

    system_prompt = (
        "You help users query their AWS RDS configurations.\n"
        f"The available RDS instances are: {instance_list_str}.\n"
        "Try to match the user's query to the most similar RDS instance name, even if the name is not typed exactly."
        " For example, 'database one' might match 'database-1'."
        " If no reasonable match is found, politely tell the user the instance is not available."
    )

    # Call OpenAI with dynamic system prompt + full chat history
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            *request.session["messages"]
        ],
        functions=functions
    )

    choice = response.choices[0]

    if choice.finish_reason == "function_call":
        # Model wants to call a function
        function_call = choice.message.function_call
        arguments = json.loads(function_call.arguments)

        print(arguments)

        if "queries" in arguments:
            # New: Run your function safely with the list of queries
            result = fetch_rds_fields(arguments["queries"])
        else:
            # Bad arguments
            result = "Invalid function call arguments."

        # Second OpenAI call: give function output
        final_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                *request.session["messages"],
                choice.message,  # function call
                {
                    "role": "function",
                    "name": function_call.name,
                    "content": json.dumps(result)
                }
            ]
        )

        # Final LLM reply after seeing function result
        ai_response = final_completion.choices[0].message.content.strip()
        request.session["messages"].append({"role": "assistant", "content": ai_response})

    else:
        # Normal text reply
        ai_response = choice.message.content.strip()
        request.session["messages"].append({"role": "assistant", "content": ai_response})

    return JSONResponse({"ai_response": ai_response})


@app.post("/set-aws-credentials")
async def set_aws_credentials(request: Request):
    global cached_rds_data, rds_client

    credentials = await request.json()
    access_key = credentials.get("accessKeyId")
    secret_key = credentials.get("secretAccessKey")

    try:
        rds_client = boto3.client(
            'rds',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )

        # Try fetching RDS instances
        response = rds_client.describe_db_instances()
        cached_rds_data = response['DBInstances']

        # Build intro message
        if cached_rds_data:
            num_instances = len(cached_rds_data)
            instance_word = "instance" if num_instances == 1 else "instances"
            intro_message = (
                f"Hello! You have {num_instances} RDS {instance_word}.\n"
                "What would you like to know about it?\n"
                "I can answer questions like:\n"
                "- Does my RDS instance have backups enabled?\n"
                "- Is encryption turned on?\n"
                "- What engine version is it using?"
            )
        else:
            intro_message = (
                "Hello! It looks like you don't have any RDS instances in your AWS account.\n"
                "Please create one if you want to query its configuration!"
            )

        return {"success": True, "intro_message": intro_message}

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=400)

@app.post("/load-mock-data")
async def load_mock_data(request: Request):
    global cached_rds_data

    cached_rds_data = get_mock_rds_data()
    using_mock_data = True 

    intro_message = (
        f"Hello! You have {len(cached_rds_data)} mock RDS instances: proto-db and test-db.\n"
        "What would you like to know about them?\n"
        "I can answer questions like:\n"
        "- Does my RDS instance have backups enabled?\n"
        "- Is encryption turned on?\n"
        "- What engine version is it using?"
    )

    return {"success": True, "intro_message": intro_message}