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
import { useLoginMutation } from "@/lib/api/auth/auth.api";
import { toast } from "sonner";
import AuthBackground from "@/components/ui/authBackground";

const loginSchema = z.object({
  username_or_email: z.string().min(1, "Email or username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LogInPage() {
  const router = useRouter();
  const [login, { isLoading }] = useLoginMutation();

  const {
    register: formRegister,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    mode: "onTouched",
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data).unwrap();
      router.push("/");
    } catch (e) {
      toast.error("Oops! Unable to login");
    }
  };

  return (
    <>
      <AuthBackground>
        <Card className="min-w-sm max-w-md bg-card/50 font-quicksand ">
          <CardHeader>
            <CardTitle>Login to your account</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="flex flex-col gap-6">
                <div className="grid gap-2">
                  <Label htmlFor="email">Email or Username</Label>
                  <Input
                    id="email"
                    type="text"
                    placeholder="m@example.com or username"
                    {...formRegister("username_or_email", {
                      required: "Email or username is required",
                    })}
                  />
                  {errors.username_or_email && (
                    <p className="text-sm text-red-600">
                      {errors.username_or_email.message}
                    </p>
                  )}
                </div>

                <div className="grid gap-2">
                  <div className="flex items-center">
                    <Label htmlFor="password">Password</Label>
                    <a
                      href="#"
                      className="hidden ml-auto text-sm underline-offset-4 hover:underline"
                    >
                      Forgot your password?
                    </a>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    {...formRegister("password", {
                      required: "Password is required",
                    })}
                  />
                  {errors.password && (
                    <p className="text-sm text-red-600">
                      {errors.password.message}
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-6" />

              <div className="flex flex-col gap-2">
                <Button type="submit" className="w-full" disabled={isLoading}>
                  Login
                </Button>

                <a
                  href={`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/google/login`}
                >
                  <Button variant="outline" className="w-full">
                    <Image
                      src="/google__icon.png"
                      alt="Google Icon"
                      width={16}
                      height={16}
                    />
                    Login with Google
                  </Button>
                </a>

                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => router.push("/register")}
                >
                  Sign Up
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </AuthBackground>
    </>
  );
}
