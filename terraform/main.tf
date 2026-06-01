resource "alicloud_instance" "web_batch" {
  instance_name = "ecs-prod-web-batch"
  instance_type = "ecs.g7.large"    # 2 vCPUs, 8GB RAM
}
