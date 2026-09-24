terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"  #replace with your bucket name
    key            = "auftrag4.terraform.tfstate" 
    region         = "us-east-1"
  }
}
