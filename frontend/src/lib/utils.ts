export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleString()
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'ready':
      return 'text-green-600 bg-green-100'
    case 'processing':
      return 'text-blue-600 bg-blue-100'
    case 'error':
    case 'failed':
      return 'text-red-600 bg-red-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}
