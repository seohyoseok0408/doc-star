import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export function SignupForm({
  className,
  formData,
  onChange,
  onSubmit,
}: {
  className?: string;
  formData: {
    username: string;
    nickname: string;
    email: string;
    password: string;
    confirmPassword: string;
  };
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <Card className={cn("", className)}>
      <CardHeader>
        <CardTitle>Create an account</CardTitle>
        <CardDescription>Enter your information below to create your account</CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={onSubmit}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="username">* Username</FieldLabel>
              <Input
                id="username"
                type="text"
                required
                value={formData.username}
                onChange={onChange}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="nickname">* Nickname</FieldLabel>
              <Input
                id="nickname"
                type="text"
                required
                value={formData.nickname}
                onChange={onChange}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="email">* Email</FieldLabel>
              <Input id="email" type="email" required value={formData.email} onChange={onChange} />
              <FieldDescription>We&apos;ll use this to contact you.</FieldDescription>
            </Field>

            <Field>
              <FieldLabel htmlFor="password">* Password</FieldLabel>
              <Input
                id="password"
                type="password"
                required
                value={formData.password}
                onChange={onChange}
              />
              <FieldDescription>Must be at least 8 characters long.</FieldDescription>
            </Field>

            <Field>
              <FieldLabel htmlFor="confirmPassword">* Confirm Password</FieldLabel>
              <Input
                id="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={onChange}
              />
              <FieldDescription>Please confirm your password.</FieldDescription>
            </Field>

            <Field>
              <Button type="submit">Create Account</Button>
              <Button variant="outline" type="button">
                Sign up with Google
              </Button>
              <FieldDescription className="px-6 text-center">
                Already have an account? <Link to="/login">Sign in</Link>
              </FieldDescription>
            </Field>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
