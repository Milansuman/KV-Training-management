"use client";

import { useState } from "react";
import {
  Bot,
  ExternalLink,
  File,
  Link,
  Plus,
  Trash2,
  Pencil,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

import {
  useGetTrainingMaterialsBySessionQuery,
  useUploadTrainingMaterialMutation,
  useCreateMaterialFromUrlMutation,
  useUpdateTrainingMaterialMutation,
  useDeleteTrainingMaterialMutation,
} from "@/lib/api/training-materials/training-materials.api";
import type { TrainingMaterialResponse } from "@/lib/api/training-materials/training-materials.type";
import type { UserResponse } from "@/lib/api/user/user.type";
import type { TopicResponse } from "@/lib/api/sessions/sessions.type";

import { useAnalyzeTrainingMaterialMutation } from "@/lib/api/ai/training-materials.api";

function getErrorDetail(err: unknown): string {
  const data = (err as { data?: { detail?: string; message?: string } })?.data;
  return data?.detail || data?.message || "An error occurred";
}

interface TrainingMaterialsSectionProps {
  sessionId: number;
  user: UserResponse | undefined;
  canManage: boolean;
  topics?: TopicResponse[];
}

export default function TrainingMaterialsSection({
  sessionId,
  user,
  canManage,
  topics = [],
}: TrainingMaterialsSectionProps) {
  const { data: materials = [], isLoading: materialsLoading } =
    useGetTrainingMaterialsBySessionQuery(sessionId);
  const [uploadMaterial, { isLoading: isUploading }] =
    useUploadTrainingMaterialMutation();
  const [createFromUrl, { isLoading: isCreatingUrl }] =
    useCreateMaterialFromUrlMutation();
  const [updateMaterial, { isLoading: isUpdatingMaterial }] =
    useUpdateTrainingMaterialMutation();
  const [deleteMaterial] = useDeleteTrainingMaterialMutation();

  // Add dialog
  const [isMaterialAddOpen, setIsMaterialAddOpen] = useState(false);
  const [materialTitle, setMaterialTitle] = useState("");
  const [materialUrl, setMaterialUrl] = useState("");
  const [materialFile, setMaterialFile] = useState<File | null>(null);
  const [materialTab, setMaterialTab] = useState<"url" | "file">("url");

  // Update dialog
  const [isMaterialUpdateOpen, setIsMaterialUpdateOpen] = useState(false);
  const [editingMaterialId, setEditingMaterialId] = useState<number | null>(
    null,
  );
  const [updateMaterialTitle, setUpdateMaterialTitle] = useState("");
  const [updateMaterialUrl, setUpdateMaterialUrl] = useState("");
  const [updateMaterialFile, setUpdateMaterialFile] = useState<File | null>(null);
  const [updateMaterialTab, setUpdateMaterialTab] = useState<"url" | "file">("url");

  // Delete loading
  const [deletingMaterialId, setDeletingMaterialId] = useState<number | null>(
    null,
  );

  // AI suggestions
  const [analyzeMaterial, { isLoading: isAnalyzing }] =
    useAnalyzeTrainingMaterialMutation();
  const [aiSuggestionsMaterial, setAiSuggestionsMaterial] =
    useState<TrainingMaterialResponse | null>(null);
  const [aiSuggestionsContent, setAiSuggestionsContent] = useState<
    string | null
  >(null);
  const [aiSuggestionsError, setAiSuggestionsError] = useState<
    string | null
  >(null);

  function resetMaterialAddForm() {
    setMaterialTitle("");
    setMaterialUrl("");
    setMaterialFile(null);
    setMaterialTab("url");
  }

  async function handleAddMaterial(e: React.FormEvent) {
    e.preventDefault();
    if (!materialTitle || !user) return;

    try {
      if (materialTab === "url") {
        if (!materialUrl) {
          toast.error("Please enter a URL.");
          return;
        }
        await createFromUrl({
          title: materialTitle,
          url: materialUrl,
          session_id: sessionId,
          user_id: user.id,
        }).unwrap();
        toast.success("Material added successfully!");
      } else {
        if (!materialFile) {
          toast.error("Please select a file.");
          return;
        }
        await uploadMaterial({
          title: materialTitle,
          session_id: sessionId,
          user_id: user.id,
          file: materialFile,
        }).unwrap();
        toast.success("Material uploaded successfully!");
      }
      setIsMaterialAddOpen(false);
      resetMaterialAddForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  function handleEditMaterial(material: TrainingMaterialResponse) {
    setEditingMaterialId(material.id);
    setUpdateMaterialTitle(material.title);
    setUpdateMaterialUrl(material.url);
    setUpdateMaterialFile(null);
    setUpdateMaterialTab(material.material_type === "URL" ? "url" : "file");
    setIsMaterialUpdateOpen(true);
  }

  async function handleUpdateMaterial(e: React.FormEvent) {
    e.preventDefault();
    if (!editingMaterialId || !updateMaterialTitle) return;

    try {
      await updateMaterial({
        materialId: editingMaterialId,
        title: updateMaterialTitle,
        url: updateMaterialTab === "url" ? updateMaterialUrl : null,
        file: updateMaterialTab === "file" ? updateMaterialFile : null,
      }).unwrap();
      toast.success("Material updated successfully!");
      setIsMaterialUpdateOpen(false);
      setEditingMaterialId(null);
      setUpdateMaterialTitle("");
      setUpdateMaterialUrl("");
      setUpdateMaterialFile(null);
      setUpdateMaterialTab("url");
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  async function handleDeleteMaterial(materialId: number) {
    if (!confirm("Are you sure you want to delete this material?")) return;
    setDeletingMaterialId(materialId);
    try {
      await deleteMaterial(materialId).unwrap();
      toast.success("Material deleted!");
    } catch (err) {
      toast.error(getErrorDetail(err));
    } finally {
      setDeletingMaterialId(null);
    }
  }

  async function handleGetAiSuggestions(material: TrainingMaterialResponse) {
    setAiSuggestionsMaterial(material);
    setAiSuggestionsContent(null);
    setAiSuggestionsError(null);
    try {
      const result = await analyzeMaterial({
        material_url: material.url,
        topics: topics?.map((t) => t.title) ?? [],
      }).unwrap();
      setAiSuggestionsContent(result.suggestions);
    } catch (err) {
      const detail = getErrorDetail(err);
      setAiSuggestionsError(detail);
    }
  }

  function resetAiSuggestions() {
    setAiSuggestionsMaterial(null);
    setAiSuggestionsContent(null);
    setAiSuggestionsError(null);
  }

  return (
    <div className="flex flex-col gap-6 mt-4">
      <div className="flex items-center justify-between">
        {canManage && (
          <Dialog
            open={isMaterialAddOpen}
            onOpenChange={(open) => {
              setIsMaterialAddOpen(open);
              if (!open) resetMaterialAddForm();
            }}
          >
            <DialogTrigger
              render={
                <Button>
                  <Plus data-icon="inline-start" />
                  Add Material
                </Button>
              }
            />
          <DialogContent className="sm:max-w-md">
            <form onSubmit={handleAddMaterial}>
              <DialogHeader>
                <DialogTitle>Add Training Material</DialogTitle>
                <DialogDescription>
                  Provide a title and either a URL or upload a file.
                </DialogDescription>
              </DialogHeader>
              <div className="flex flex-col gap-4 py-4">
                <div className="flex flex-col gap-2">
                  <Label>
                    Title <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    placeholder="e.g. Course Slides"
                    value={materialTitle}
                    onChange={(e) => setMaterialTitle(e.target.value)}
                    required
                  />
                </div>
                <Tabs
                  value={materialTab}
                  onValueChange={(v) =>
                    setMaterialTab(v as "url" | "file")
                  }
                >
                  <TabsList className="w-full" variant="line">
                    <TabsTrigger className="flex-1" value="url">
                      URL
                    </TabsTrigger>
                    <TabsTrigger className="flex-1" value="file">
                      File Upload
                    </TabsTrigger>
                  </TabsList>
                  <TabsContent value="url">
                    <Input
                      placeholder="https://example.com/material"
                      value={materialUrl}
                      onChange={(e) => setMaterialUrl(e.target.value)}
                    />
                  </TabsContent>
                  <TabsContent value="file">
                    <Input
                      type="file"
                      onChange={(e) =>
                        setMaterialFile(e.target.files?.[0] ?? null)
                      }
                    />
                  </TabsContent>
                </Tabs>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsMaterialAddOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isUploading || isCreatingUrl}
                >
                  {(isUploading || isCreatingUrl) && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {materialTab === "url" ? "Add URL" : "Upload File"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
        )}
      </div>

      {materialsLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : materials.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No materials yet.</p>
          <p className="text-sm">Add one to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {materials.map((material) => (
            <div key={material.id}>
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    {material.material_type === "URL" ? (
                      <Link className="size-4 shrink-0 text-muted-foreground" />
                    ) : (
                      <File className="size-4 shrink-0 text-muted-foreground" />
                    )}
                    <CardTitle>{material.title}</CardTitle>
                  </div>
                  <CardDescription>
                    {material.material_type === "URL"
                      ? material.url
                      : material.url
                        ? material.url.split("/").pop()
                        : "FILE"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                    {material.material_type === "URL" ? (
                      <>
                        <Link className="size-3" />
                        URL
                      </>
                    ) : (
                      <>
                        <File className="size-3" />
                        File
                      </>
                    )}
                  </span>
                </CardContent>
                <CardFooter>
                  {material.material_type === "URL" ? (
                    <a
                      href={material.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button size="sm" variant="ghost" type="button">
                        <ExternalLink data-icon="inline-start" />
                        Open
                      </Button>
                    </a>
                  ) : (
                    <a
                      href={material.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button size="sm" variant="ghost" type="button">
                        <File data-icon="inline-start" />
                        Download
                      </Button>
                    </a>
                  )}
                  {canManage && (
                    <div className="ml-auto flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => handleGetAiSuggestions(material)}
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                      >
                        <Bot className="size-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleEditMaterial(material)}
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                      >
                        <Pencil className="size-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteMaterial(material.id)}
                        disabled={deletingMaterialId === material.id}
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                      >
                        {deletingMaterialId === material.id ? (
                          <Loader2 className="size-4 animate-spin" />
                        ) : (
                          <Trash2 className="size-4" />
                        )}
                      </button>
                    </div>
                  )}
                </CardFooter>
              </Card>

              {/* ── AI Suggestions Dialog ───────────────── */}
              <Dialog
                open={
                  aiSuggestionsMaterial?.id === material.id &&
                  !isMaterialUpdateOpen
                }
                onOpenChange={(open) => {
                  if (!open) resetAiSuggestions();
                }}
              >
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <div className="flex items-center gap-2">
                      <div className="flex size-8 items-center justify-center rounded-full bg-primary/10">
                        <Bot className="size-4 text-primary" />
                      </div>
                      <DialogTitle>
                        AI Suggestions — {aiSuggestionsMaterial?.title}
                      </DialogTitle>
                    </div>
                    <DialogDescription>
                      Analysis of clarity, structure, and completeness.
                    </DialogDescription>
                  </DialogHeader>
                  {isAnalyzing ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    </div>
                  ) : aiSuggestionsError ? (
                    <p className="text-sm text-destructive">
                      {aiSuggestionsError}
                    </p>
                  ) : aiSuggestionsContent ? (
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/80">
                      {aiSuggestionsContent}
                    </p>
                  ) : null}
                  <DialogFooter>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetAiSuggestions}
                    >
                      Close
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              {/* ── Update Material Dialog ────────────────── */}
              <Dialog
                open={
                  isMaterialUpdateOpen &&
                  editingMaterialId === material.id
                }
                onOpenChange={(open) => {
                  setIsMaterialUpdateOpen(open);
                  if (!open) {
                    setEditingMaterialId(null);
                    setUpdateMaterialTitle("");
                    setUpdateMaterialUrl("");
                    setUpdateMaterialFile(null);
                    setUpdateMaterialTab("url");
                  }
                }}
              >
                <DialogContent className="sm:max-w-md">
                  <form onSubmit={handleUpdateMaterial}>
                    <DialogHeader>
                      <DialogTitle>Edit Material</DialogTitle>
                      <DialogDescription>
                        Update the details for this material.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="flex flex-col gap-4 py-4">
                      <div className="flex flex-col gap-2">
                        <Label htmlFor="update-mat-title">
                          Title{" "}
                          <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id="update-mat-title"
                          placeholder="e.g. Course Slides"
                          value={updateMaterialTitle}
                          onChange={(e) =>
                            setUpdateMaterialTitle(e.target.value)
                          }
                          required
                        />
                      </div>
                      <Tabs value={updateMaterialTab} onValueChange={(v) => setUpdateMaterialTab(v as "url" | "file")}>
                        <TabsList className="w-full" variant="line">
                          <TabsTrigger className="flex-1" value="url">
                            URL
                          </TabsTrigger>
                          <TabsTrigger className="flex-1" value="file">
                            File Upload
                          </TabsTrigger>
                        </TabsList>
                        <TabsContent value="url">
                          <Input
                            placeholder="https://example.com/material"
                            value={updateMaterialUrl}
                            onChange={(e) =>
                              setUpdateMaterialUrl(e.target.value)
                            }
                          />
                        </TabsContent>
                        <TabsContent value="file">
                          <Input
                            type="file"
                            onChange={(e) => {
                              const file = (e.target as HTMLInputElement).files?.[0] || null;
                              setUpdateMaterialFile(file);
                            }}
                          />
                        </TabsContent>
                      </Tabs>
                    </div>
                    <DialogFooter>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                            setIsMaterialUpdateOpen(false);
                            setEditingMaterialId(null);
                            setUpdateMaterialTitle("");
                            setUpdateMaterialUrl("");
                            setUpdateMaterialFile(null);
                            setUpdateMaterialTab("url");
                          }}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        disabled={isUpdatingMaterial}
                      >
                        {isUpdatingMaterial && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Update Material
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
