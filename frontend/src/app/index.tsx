import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/axios";

interface ExtractDataRequest {
  url: string;
  prompt: string;
}

type ExtractDataResponse = {
  schema_used: any;
  data: any;
};

const extractData = async (
  request: ExtractDataRequest,
): Promise<ExtractDataResponse> => {
  const response = await api.post<ExtractDataResponse>("/", request);
  return response.data;
};

const App = () => {
  const [url, setUrl] = useState("");
  const [prompt, setPrompt] = useState("");

  const {
    mutate: extract,
    data: result,
    isPending,
    error,
    reset,
  } = useMutation({
    mutationFn: extractData,
    onError: (err: any) => {
      console.error("Extraction error:", err);
    },
  });

  const handleExtract = () => {
    if (!url || !prompt) {
      return;
    }

    reset(); // Clear previous results
    extract({ url, prompt });
  };

  return (
    <div className="min-h-screen bg-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-black mb-1">ParseBot</h1>
          <p className="text-muted-foreground">
            Extract structured data from any website using AI
          </p>
        </div>

        <div className="bg-white rounded-lg border border-border p-6 shadow-sm">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Website URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-3 py-2 bg-white border border-input rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">
                Extraction Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="What data would you like to extract? (e.g., 'get all product names and prices')"
                rows={4}
                className="w-full px-3 py-2 bg-white border border-input rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 resize-none"
              />
            </div>

            <button
              onClick={handleExtract}
              disabled={isPending || !url || !prompt}
              className="w-full py-2.5 px-4 bg-black hover:bg-black/90 disabled:bg-muted text-white font-medium rounded-md transition-colors disabled:cursor-not-allowed disabled:text-muted-foreground"
            >
              {isPending ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Extracting...
                </span>
              ) : (
                "Extract Data"
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
              <p className="text-sm text-destructive">
                {error instanceof Error ? error.message : "Failed to extract data"}
              </p>
            </div>
          )}

          {result && (
            <div className="mt-6 space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">
                  Generated Schema
                </h3>
                <pre className="bg-muted p-3 rounded-md overflow-x-auto text-xs text-foreground border border-border">
                  {JSON.stringify(result.schema_used, null, 2)}
                </pre>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">
                  Extracted Data
                </h3>
                <pre className="bg-muted p-3 rounded-md overflow-x-auto text-xs text-foreground border border-border max-h-96 overflow-y-auto">
                  {typeof result.data === "string"
                    ? result.data
                    : JSON.stringify(result.data, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
