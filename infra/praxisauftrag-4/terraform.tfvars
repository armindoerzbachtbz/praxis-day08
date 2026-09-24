# Optional: make resource names unique.
student_name = "ado"

## In Praxisauftrag 4 the CI/CD pipeline derives this public key from
## the EC2_SSH_KEY secret and passes it to OpenTofu with -var.
 ssh_public_key_path = "/tmp/techstyle_ec2.pub"
