import React from 'react'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'
import EditorToolbar, { quillModules, quillFormats } from './EditorToolbar'

export default function Editor({ value, onChange }) {
  return (
    <div className="w-full">
      <EditorToolbar />
      <ReactQuill
        theme="snow"
        value={value}
        onChange={onChange}
        placeholder="Escribe tu texto aquí..."
        modules={quillModules}
        formats={quillFormats}
        className="bg-white rounded-xl"
      />
    </div>
  )
}

