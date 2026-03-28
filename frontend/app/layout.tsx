import '../styles/globals.css'

export const metadata = {
  title: 'AuraX App',
  description: 'AI-Powered Hyper-Local Fashion Intelligence',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0',
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
