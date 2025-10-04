export default function Footer() {
  return (
    <footer className="px-6 border-t border-black/[.08] dark:border-white/[.12]">
      <div className="mx-auto w-full max-w-6xl py-8 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="text-sm">© {new Date().getFullYear()} CoinSense</div>
        <div className="text-sm text-black/70 dark:text-white/70">Built with care</div>
      </div>
    </footer>
  );
}


