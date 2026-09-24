terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket-679328225347-us-east-1-an"  #replace with your bucket name
    key            = "auftrag4.terraform.tfstate" 
    region         = "us-east-1"
  }
}
