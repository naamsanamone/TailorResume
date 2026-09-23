import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

/**
 * Home page — redirects straight to the Resume Builder.
 * No landing page needed for Chrome extension integration.
 */
function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/builder');
  }, [router]);

  return (
    <Head>
      <title>TailorResume</title>
      <meta name="description" content="AI-powered resume builder & tailor" />
      <link rel="icon" type="image/png" href="/icons/resume-icon.png" />
    </Head>
  );
}

export default HomePage;
