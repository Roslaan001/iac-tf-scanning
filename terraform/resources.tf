# Security Group with deliberate IaC misconfigurations for scanning
resource "aws_security_group" "vulnerable_sg" {
  name        = "vulnerable-app-sg"
  description = "Security group for application with permissive ingress"
  vpc_id      = data.aws_vpc.default.id

  # MISCONFIGURATION 8: Open SSH access to the world (0.0.0.0/0)
  ingress {
    description = "SSH access from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # MISCONFIGURATION 9: Unrestricted egress traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "vulnerable-app-sg"
    Environment = "test"
  }
}

# IAM Role with wildcard/overly-permissive policy for IaC scanning
resource "aws_iam_role" "vulnerable_role" {
  name = "vulnerable-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# MISCONFIGURATION 10: IAM Policy with AdministratorAccess / wildcard permissions (AVD-AWS-0057)
resource "aws_iam_role_policy" "vulnerable_policy" {
  name = "vulnerable-app-policy"
  role = aws_iam_role.vulnerable_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

# RDS DB Instance with deliberate IaC misconfigurations
resource "aws_db_instance" "vulnerable_db" {
  allocated_storage      = 20
  identifier             = "vulnerable-rds-instance"
  db_name                = "appdb"
  engine                 = "postgres"
  engine_version         = "15.7"
  instance_class         = "db.t3.micro"
  username               = "dbadmin"
  password               = "SuperSecretPass123!" # Hardcoded credentials check
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.vulnerable_sg.id]

  # MISCONFIGURATION 11: Storage Encryption Disabled (AVD-AWS-0133)
  storage_encrypted = false

  # MISCONFIGURATION 12: Public Access Allowed (AVD-AWS-0177)
  publicly_accessible = true

  # MISCONFIGURATION 13: Auto Minor Version Upgrade Disabled (AVD-AWS-0178)
  auto_minor_version_upgrade = false

  # MISCONFIGURATION 14: IAM Database Authentication Disabled (AVD-AWS-0176)
  iam_database_authentication_enabled = false

  # MISCONFIGURATION 15: Deletion Protection Disabled (AVD-AWS-0175)
  deletion_protection = false

  tags = {
    Name        = "vulnerable-rds-instance"
    Environment = "test"
  }
}
