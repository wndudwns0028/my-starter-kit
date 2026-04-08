variable "cluster_name" {
  description = "EKS 클러스터 이름"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes 버전"
  type        = string
  default     = "1.31"
}

variable "vpc_id" {
  description = "EKS를 배포할 VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "EKS 노드 서브넷 ID 목록 (최소 2개 AZ)"
  type        = list(string)
}

variable "enable_gpu_nodegroup" {
  description = "GPU 노드그룹 활성화 여부"
  type        = bool
  default     = false
}

variable "gpu_instance_type" {
  description = "GPU 인스턴스 타입"
  type        = string
  default     = "g4dn.xlarge"    # NVIDIA T4, 16GB VRAM
}
