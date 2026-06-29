import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const MESSAGES = [
  "Analyzing your Whop community...",
  "Scanning member reviews & complaints...",
  "Identifying retention gaps...",
  "Designing your custom retention tool...",
  "Almost done...",
];

export default function LoadingScreen() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setI((v) => (v + 1) % MESSAGES.length), 1500);
    return () => clearInterval(id);
  }, []);
  return (
    <div
      data-testid="loading-screen"
      className="fixed inset-0 z-40 flex flex-col items-center justify-center bg-[#0F0F11]/95 backdrop-blur-md bg-glow"
    >
      <div className="relative">
        <div className="absolute inset-0 rounded-full bg-[#FF4F00]/30 blur-2xl animate-pulse-glow" />
        <div className="relative h-16 w-16 rounded-full border-2 border-[#27272A] border-t-[#FF4F00] animate-spin" />
      </div>
      <div className="mt-10 h-7 overflow-hidden text-center">
        <AnimatePresence mode="wait">
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.35 }}
            className="font-display text-base sm:text-lg text-white"
          >
            {MESSAGES[i]}
          </motion.div>
        </AnimatePresence>
      </div>
      <div className="mt-2 text-xs uppercase tracking-[0.25em] text-whop-mute">App Builders Engine</div>
    </div>
  );
}
