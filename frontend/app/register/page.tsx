"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRegisterMutation } from "@/lib/api/auth/auth.api";
import { toast } from "sonner"

const registerSchema = z
  .object({
    username: z.string().min(1, "Username is required"),
    display_name: z.string().min(1, "Display name is required"),
    email: z.string().email("Invalid email"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirm_password, {
    path: ["confirm_password"],
    message: "Passwords do not match",
  });

type FormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [registerUser, { isLoading }] = useRegisterMutation();

  const {
    register: formRegister,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ mode: "onTouched", resolver: zodResolver(registerSchema) });

  const onSubmit = async (data: FormValues) => {
    try {
      await registerUser({
        username: data.username,
        email: data.email,
        display_name: data.display_name,
        password: data.password,
      }).unwrap();
      router.push("/login");
    } catch (e) {
      toast.error("Failed to create an account");
    }
  };


  return (
    <>
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-full max-w-sm">
          <CardHeader>
            <CardTitle>Create an account</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="flex flex-col gap-6">
                <div className="grid gap-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    {...formRegister("username", { required: "Username is required" })}
                    placeholder="@m_s"
                  />
                  {errors.username && (
                    <p className="text-sm text-red-600">{errors.username.message}</p>
                  )}
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="display_name">Display Name</Label>
                  <Input
                    id="display_name"
                    {...formRegister("display_name", { required: "Display name is required" })}
                    placeholder="Firstname Lastname"
                  />
                  {errors.display_name && (
                    <p className="text-sm text-red-600">{errors.display_name.message}</p>
                  )}
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    {...formRegister("email", {
                      required: "Email is required",
                      pattern: { value: /^[^@\s]+@[^@\s]+\.[^@\s]+$/, message: "Invalid email" },
                    })}
                    placeholder="m@example.com"
                  />
                  {errors.email && (
                    <p className="text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    {...formRegister("password")}
                  />
                  {errors.password && (
                    <p className="text-sm text-red-600">{errors.password.message}</p>
                  )}
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="confirm_password">Confirm Password</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    {...formRegister("confirm_password")}                  />
                  {errors.confirm_password && (
                    <p className="text-sm text-red-600">{errors.confirm_password.message}</p>
                  )}
                </div>
              </div>

              <div className="mt-6" />

              <div className="flex flex-col gap-2">
                <Button type="submit" className="w-full" disabled={isLoading}>
                  Sign Up
                </Button>

                <a href={`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/google/login`}>
                  <Button variant="outline" className="w-full">
                    <Image src="/google__icon.png" alt="Google Icon" width={16} height={16} />
                    Sign Up with Google
                  </Button>
                </a>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
