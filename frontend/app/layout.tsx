import './globals.css'; 
import Navbar from '../components/Navbar'; 

export const metadata = {
  title: 'The Bonel Project',
  description: 'Science Without Borders.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <div className="pt-14"> 
          {children}
        </div>
      </body>
    </html>
  );
}