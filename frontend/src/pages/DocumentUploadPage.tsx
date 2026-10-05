import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiUpload, extractErrorInfo } from "@/utils/apiClient";

export default function DocumentUploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [isError, setIsError] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setUploadStatus("");
    } else {
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("파일을 선택해주세요.");
      setIsError(true);
      return;
    }

    setLoading(true);
    setUploadStatus("");
    setIsError(false);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await apiUpload<string>("/api/document/upload", formData);

      setUploadStatus(response || `'${selectedFile.name}' 파일이 성공적으로 업로드되었습니다.`);
      setSelectedFile(null); // Clear selected file after successful upload
    } catch (error) {
      const { message: errorMessage } = extractErrorInfo(error);
      setUploadStatus(errorMessage);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">문서 업로드</CardTitle>
          <CardDescription className="text-center">
            AI 검색을 위해 문서를 업로드해주세요.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full items-center gap-1.5">
            <label htmlFor="document-upload" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              파일 선택
            </label>
            <Input
              id="document-upload"
              type="file"
              onChange={handleFileChange}
              disabled={loading}
              className="file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground file:border-none file:rounded-md file:mr-4 file:py-2 file:px-4"
            />
            {selectedFile && (
              <p className="text-sm text-muted-foreground mt-1">선택된 파일: {selectedFile.name}</p>
            )}
          </div>
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            className="w-full"
          >
            {loading ? "업로드 중..." : "업로드"}
          </Button>
          {uploadStatus && (
            <p className={`text-center text-sm ${isError ? "text-destructive" : "text-success"}`}>
              {uploadStatus}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
