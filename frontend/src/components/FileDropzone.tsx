import { useState, useRef } from 'react'

interface FileDropzoneProps {
  onFileSelect: (file: File) => void
  uploading: boolean
}

export default function FileDropzone({ onFileSelect, uploading }: FileDropzoneProps) {
  const [dragging, setDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) onFileSelect(file)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFileSelect(file)
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
        dragging
          ? 'border-blue-500 bg-blue-50'
          : 'border-slate-300 bg-white hover:border-slate-400'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.docx,.xlsx,.csv,.jpg,.jpeg,.png,.txt"
        disabled={uploading}
      />
      <svg
        className="mx-auto h-12 w-12 text-slate-400 mb-4"
        stroke="currentColor"
        fill="none"
        viewBox="0 0 48 48"
      >
        <path
          d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <p className="text-slate-600 font-medium mb-2">
        {uploading ? 'Učitavanje...' : 'Kliknite ili prevucite fajl za učitavanje'}
      </p>
      <p className="text-sm text-slate-500">
        Podržava PDF, DOCX, XLSX, CSV, JPG, PNG (Maks 50MB)
      </p>
    </div>
  )
}
