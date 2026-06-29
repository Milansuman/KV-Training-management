import DotGrid from "../background/DotGrid";

export default function AuthBackground({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="relative min-h-screen bg-background text-foreground">

            <div className="absolute inset-0">
                <DotGrid
                    dotSize={2}
                    gap={15}
                    baseColor="#2F293A"
                    activeColor="#2757ff"
                    proximity={120}
                    shockRadius={250}
                    shockStrength={5}
                    resistance={750}
                    returnDuration={1.5}
                />
            </div>

            <div className="relative z-10 flex items-center justify-center min-h-screen">
                {children}
            </div>

        </div>
    );
}