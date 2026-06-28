import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Image from "next/image"



export default function register()
{

  return (
    <>
        <div className="flex items-center justify-center min-h-screen">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle>Create an account</CardTitle>
                    <CardDescription>
                        Enter the following details to create an account
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form>
                        <div className="flex flex-col gap-6">
                            <div className="grid gap-2">
                                <Label htmlFor="username">Username</Label>
                                <Input
                                    id="username"
                                    type="text"
                                    placeholder="@m_s"
                                    required
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="email">Display Name</Label>
                                <Input
                                    id="display_name"
                                    type="text"
                                    placeholder="Firstname Lastname"
                                    required
                                />
                            </div>
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
                                className="hidden ml-autotext-sm underline-offset-4 hover:underline"
                                >
                                Forgot your password?
                                </a>
                            </div>
                            <Input id="password" type="password" required />
                            </div>
                        </div>
                    </form>
                </CardContent>
                <CardFooter className="flex-col gap-2">
                    <Button type="submit" className="w-full">
                        Sign Up
                    </Button>
                    <Button variant="outline" className="w-full">
                        <Image
                            src="/google__icon.png"
                            alt="Google Icon"
                            width={16}
                            height={16}
                            />
                        Sign Up with Google
                    </Button>
                </CardFooter>
            </Card>
        </div>
            
    </>
    )
}