import AppNavbar from "../../components/ui/appNavbar";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AppNavbar />

      <main className="pt-24">
        {children}
      </main>
    </>
  );
}