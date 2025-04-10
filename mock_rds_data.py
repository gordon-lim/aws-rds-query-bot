from datetime import datetime

def get_mock_rds_data():
    now = datetime.utcnow()

    return [
        {
            "DBInstanceIdentifier": "proto-db",
            "DBInstanceClass": "db.t3.micro",
            "Engine": "mysql",
            "DBInstanceStatus": "available",
            "MasterUsername": "admin",
            "Endpoint": {"Address": "proto-db.abc123xyz.us-east-1.rds.amazonaws.com", "Port": 3306},
            "AllocatedStorage": 20,
            "InstanceCreateTime": now,
            "PreferredBackupWindow": "03:00-03:30",
            "BackupRetentionPeriod": 7,
            "DBSecurityGroups": [],
            "VpcSecurityGroups": [],
            "DBParameterGroups": [],
            "AvailabilityZone": "us-east-1a",
            "DBSubnetGroup": {},
            "PreferredMaintenanceWindow": "sun:05:00-sun:05:30",
            "PendingModifiedValues": {},
            "LatestRestorableTime": now,
            "MultiAZ": False,
            "EngineVersion": "8.0.28",
            "AutoMinorVersionUpgrade": True,
            "ReadReplicaDBInstanceIdentifiers": [],
            "LicenseModel": "general-public-license",
            "OptionGroupMemberships": [],
            "PubliclyAccessible": True,
            "StorageType": "gp2",
            "DbInstancePort": 3306,
            "StorageEncrypted": True,
            "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/abc12345-6789-0123-4567-abcdef123456",
            "DbiResourceId": "db-ABC123DEF456GHI789",
            "CACertificateIdentifier": "rds-ca-2019",
            "DomainMemberships": [],
            "CopyTagsToSnapshot": True,
            "MonitoringInterval": 0,
            "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:proto-db",
            "IAMDatabaseAuthenticationEnabled": False,
            "DatabaseInsightsMode": "enabled",
            "PerformanceInsightsEnabled": False,
            "DeletionProtection": False,
            "AssociatedRoles": [],
            "MaxAllocatedStorage": 100,
            "TagList": [],
            "CustomerOwnedIpEnabled": False,
            "ActivityStreamStatus": "stopped",
            "BackupTarget": "region",
            "NetworkType": "IPV4",
            "StorageThroughput": 0,
            "CertificateDetails": {},
            "DedicatedLogVolume": False,
            "IsStorageConfigUpgradeAvailable": False,
            "EngineLifecycleSupport": "supported"
        },
        {
            "DBInstanceIdentifier": "test-db",
            "DBInstanceClass": "db.t3.small",
            "Engine": "postgres",
            "DBInstanceStatus": "available",
            "MasterUsername": "postgresadmin",
            "Endpoint": {"Address": "test-db.def456uvw.us-east-1.rds.amazonaws.com", "Port": 5432},
            "AllocatedStorage": 30,
            "InstanceCreateTime": now,
            "PreferredBackupWindow": "04:00-04:30",
            "BackupRetentionPeriod": 1,
            "DBSecurityGroups": [],
            "VpcSecurityGroups": [],
            "DBParameterGroups": [],
            "AvailabilityZone": "us-east-1b",
            "DBSubnetGroup": {},
            "PreferredMaintenanceWindow": "sat:06:00-sat:06:30",
            "PendingModifiedValues": {},
            "LatestRestorableTime": now,
            "MultiAZ": True,
            "EngineVersion": "13.4",
            "AutoMinorVersionUpgrade": True,
            "ReadReplicaDBInstanceIdentifiers": [],
            "LicenseModel": "postgresql-license",
            "OptionGroupMemberships": [],
            "PubliclyAccessible": False,
            "StorageType": "gp3",
            "DbInstancePort": 5432,
            "StorageEncrypted": False,
            "KmsKeyId": None,
            "DbiResourceId": "db-XYZ789ABC456DEF123",
            "CACertificateIdentifier": "rds-ca-rsa2048-g1",
            "DomainMemberships": [],
            "CopyTagsToSnapshot": True,
            "MonitoringInterval": 0,
            "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:test-db",
            "IAMDatabaseAuthenticationEnabled": True,
            "DatabaseInsightsMode": "disabled",
            "PerformanceInsightsEnabled": True,
            "DeletionProtection": True,
            "AssociatedRoles": [],
            "MaxAllocatedStorage": 200,
            "TagList": [],
            "CustomerOwnedIpEnabled": False,
            "ActivityStreamStatus": "stopped",
            "BackupTarget": "region",
            "NetworkType": "IPV4",
            "StorageThroughput": 0,
            "CertificateDetails": {},
            "DedicatedLogVolume": True,
            "IsStorageConfigUpgradeAvailable": True,
            "EngineLifecycleSupport": "supported"
        }
    ]
