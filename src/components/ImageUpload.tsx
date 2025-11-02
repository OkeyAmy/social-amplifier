import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Upload, X } from "lucide-react";

interface ImageUploadProps {
  onSubmit: (file: File | null, preview: string | null) => void;
  onBack: () => void;
}

const ImageUpload = ({ onSubmit, onBack }: ImageUploadProps) => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemove = () => {
    setImageFile(null);
    setPreview(null);
  };

  const handleSkip = () => {
    onSubmit(null, null);
  };

  const handleContinue = () => {
    onSubmit(imageFile, preview);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <Button
        onClick={onBack}
        variant="outline"
        className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
      >
        <ArrowLeft className="mr-2" /> BACK
      </Button>

      <div className="brutal-card p-6 md:p-8 bg-card">
        <h2 className="mb-6 font-bold">STEP 3: ADD IMAGE (OPTIONAL)</h2>

        {!preview ? (
          <label className="block cursor-pointer">
            <div className="brutal-border border-dashed p-12 hover:bg-muted transition-colors text-center">
              <Upload className="w-16 h-16 mx-auto mb-4" />
              <p className="text-xl font-bold mb-2">DRAG & DROP IMAGE</p>
              <p className="text-sm text-muted-foreground">or click to browse</p>
              <p className="text-xs text-muted-foreground mt-2">
                JPG, PNG, GIF, WebP (max 10MB)
              </p>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        ) : (
          <div className="brutal-card p-4 bg-accent/10 rotate-slightly">
            <div className="relative">
              <img
                src={preview}
                alt="Upload preview"
                className="w-full h-auto brutal-border"
              />
              <button
                onClick={handleRemove}
                className="absolute top-2 right-2 brutal-border brutal-shadow-sm bg-destructive text-destructive-foreground p-2 hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <p className="mt-4 text-sm font-bold text-center">
              {imageFile?.name}
            </p>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <Button
          onClick={handleSkip}
          size="lg"
          variant="outline"
          className="brutal-border brutal-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold text-lg uppercase"
        >
          SKIP THIS STEP
        </Button>
        <Button
          onClick={handleContinue}
          size="lg"
          disabled={!preview}
          className="brutal-border brutal-shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 text-lg font-bold tracking-wider disabled:opacity-50 disabled:cursor-not-allowed uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none"
        >
          CONTINUE
        </Button>
      </div>
    </div>
  );
};

export default ImageUpload;
