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
    <div className="space-y-4 sm:space-y-6 animate-in fade-in duration-500">
      <Button
        onClick={onBack}
        variant="outline"
        className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all w-full sm:w-auto min-h-[44px]"
      >
        <ArrowLeft className="mr-2 w-4 h-4 sm:w-5 sm:h-5" /> BACK
      </Button>

      <div className="brutal-card p-4 sm:p-6 md:p-8 bg-card">
        <h2 className="mb-4 sm:mb-6 font-bold text-lg sm:text-xl md:text-2xl">STEP 3: ADD IMAGE (OPTIONAL)</h2>

        {!preview ? (
          <label className="block cursor-pointer">
            <div className="brutal-border border-dashed p-6 sm:p-8 md:p-12 hover:bg-muted transition-colors text-center min-h-[200px] sm:min-h-[240px] flex flex-col justify-center">
              <Upload className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 mx-auto mb-3 sm:mb-4" />
              <p className="text-base sm:text-lg md:text-xl font-bold mb-2">DRAG & DROP IMAGE</p>
              <p className="text-xs sm:text-sm text-muted-foreground">or click to browse</p>
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
          <div className="brutal-card p-3 sm:p-4 bg-accent/10 rotate-slightly">
            <div className="relative">
              <img
                src={preview}
                alt="Upload preview"
                className="w-full h-auto brutal-border"
              />
              <button
                onClick={handleRemove}
                className="absolute top-2 right-2 brutal-border brutal-shadow-sm bg-destructive text-destructive-foreground p-2 sm:p-2.5 hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all min-h-[44px] min-w-[44px] flex items-center justify-center"
              >
                <X className="w-5 h-5 sm:w-6 sm:h-6" />
              </button>
            </div>
            <p className="mt-3 sm:mt-4 text-xs sm:text-sm font-bold text-center break-words">
              {imageFile?.name}
            </p>
          </div>
        )}
      </div>

      <div className="grid sm:grid-cols-2 gap-3 sm:gap-4">
        <Button
          onClick={handleSkip}
          size="lg"
          variant="outline"
          className="brutal-border brutal-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold text-sm sm:text-base md:text-lg uppercase min-h-[44px]"
        >
          SKIP THIS STEP
        </Button>
        <Button
          onClick={handleContinue}
          size="lg"
          disabled={!preview}
          className="brutal-border brutal-shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 text-sm sm:text-base md:text-lg font-bold tracking-wider disabled:opacity-50 disabled:cursor-not-allowed uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none min-h-[44px]"
        >
          CONTINUE
        </Button>
      </div>
    </div>
  );
};

export default ImageUpload;
