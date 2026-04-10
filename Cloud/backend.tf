terraform {
    backend "s3" {
        key          = "discord-music-bot/terraform.tfstate"
        region       = "eu-west-1"
        use_lockfile = true
        encrypt      = true
    }
}
