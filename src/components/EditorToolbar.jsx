import React from 'react'

export default function EditorToolbar() {
  return (
    <div id="toolbar" className="mb-3 flex items-center gap-2 bg-white p-2 rounded-lg border">
      <span className="ql-formats">
        <button className="ql-bold" />
        <button className="ql-italic" />
        <button className="ql-underline" />
      </span>
      <span className="ql-formats">
        <button className="ql-list" value="ordered" />
        <button className="ql-list" value="bullet" />
      </span>
      <span className="ql-formats">
        <button className="ql-link" />
      </span>
      <span className="ql-formats">
        <button className="ql-clean" />
      </span>
    </div>
  )
}
export const quillModules = { toolbar: { container: "#toolbar" } }
export const quillFormats = ["bold","italic","underline","list","bullet","link","clean"]
