import '../styles/globals.css'

export const metadata = {
  title: 'AuraX Dashboard',
  description: 'AI-Powered Hyper-Local Fashion Intelligence',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
