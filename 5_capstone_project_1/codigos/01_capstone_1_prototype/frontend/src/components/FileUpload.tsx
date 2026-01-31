import React from 'react';
import type { ChangeEvent } from 'react';
import { Upload } from 'lucide-react';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
    selectedFile: File | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, selectedFile }) => {
    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            onFileSelect(e.target.files[0]);
        }
    };

    return (
        <div className="file-upload-container">
            <div className="file-upload-header">
                <Upload size={24} className="icon" />
                <span className="title">Seleccionar Archivo</span>
            </div>

            <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="file-input"
            />

            {selectedFile && (
                <div className="file-status success">
                    Archivo seleccionado: <strong>{selectedFile.name}</strong>
                </div>
            )}
        </div>
    );
};
