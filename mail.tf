provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  endpoints {
    ec2    = "http://localhost:4566"
    s3     = "http://localhost:4566"
    iam    = "http://localhost:4566"
    lambda = "http://localhost:4566"
    ssm    = "http://localhost:4566"
    sts    = "http://localhost:4566"
    sqs    = "http://localhost:4566"
    sns    = "http://localhost:4566"
  }
}

module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 3.0"
  bucket  = "example-bucket"
  acl     = "private"

  versioning = {
    enabled = true
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Environment = "Development"
    Owner       = "User"
  }
}

module "lambda_function" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "~> 4.0"
  function_name = "example-lambda"
  handler       = "index.handler"
  runtime       = "nodejs16.x"
  source_path   = "./lambda"

  depends_on = [module.s3_bucket]
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name = "lambda-s3-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
        Effect = "Allow",
        Resource = [
          module.s3_bucket.s3_bucket_arn,
          "${module.s3_bucket.s3_bucket_arn}/*"
        ]
      }
    ]
  })

  depends_on = [module.lambda_function, module.s3_bucket]
}

resource "aws_iam_policy_attachment" "lambda_s3_policy_attachment" {
  name       = "lambda-s3-policy-attachment"
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
  roles      = [module.lambda_function.lambda_role_name]
}

resource "aws_sns_topic" "example_topic" {
  name = "example-topic"
}

resource "aws_sqs_queue" "example_queue" {
  name                       = "example-queue"
  visibility_timeout_seconds = 30
}

resource "aws_sns_topic_subscription" "example_subscription" {
  topic_arn = aws_sns_topic.example_topic.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.example_queue.arn

  depends_on = [aws_sqs_queue_policy.example_policy]
}

resource "aws_sqs_queue_policy" "example_policy" {
  queue_url = aws_sqs_queue.example_queue.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "sqs:SendMessage",
        Resource  = aws_sqs_queue.example_queue.arn,
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.example_topic.arn
          }
        }
      }
    ]
  })
}
