variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "cluster_name" {
  description = "EKS 클러스터 이름"
  type        = string
  default     = "devops-starter-cluster"
}

variable "enable_gpu_nodegroup" {
  description = "GPU 노드그룹 활성화 (Ray GPU 서빙 프로젝트 시 true)"
  type        = bool
  default     = false
}
