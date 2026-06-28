'use client'

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Image from "next/image"
import { useRouter } from "next/navigation"


export default function logIn()
{
    const router=useRouter()

    function handleSubmit()
    {
        router.push("/register")
    }

  return (
    <>
        <div className="flex items-center justify-center min-h-screen">
            <Card className="w-full max-w-sm">
                {/* CARD HEADER */}
                <CardHeader >
                    <CardTitle>Login to your account</CardTitle>
                    <CardDescription>
                        Enter your email below to login to your account
                    </CardDescription>
                </CardHeader>
                {/* CARD CONTENT */}
                <CardContent>
                    <form>
                        <div className="flex flex-col gap-6">
                            <div className="grid gap-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="m@example.com"
                                    required
                                />
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
                                <Input id="password" type="password" required />
                            </div>
                        </div>
                    </form>
                </CardContent>
                {/* CARD FOOTER */}
                <CardFooter className="flex-col gap-2">
                    <Button type="submit" className="w-full">
                        Login
                    </Button>
                    <Button variant="outline" className="w-full">
                        <Image
                            src="/google__icon.png"
                            alt="Google Icon"
                            width={16}
                            height={16}
                            />
                        Login with Google
                    </Button>
                        <Button variant="ghost" type="submit" className="w-full" onClick={handleSubmit}>Sign Up</Button>
                </CardFooter>
            </Card>
        </div>
            
    </>
    )
}