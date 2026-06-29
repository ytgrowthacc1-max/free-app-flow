import { motion } from "framer-motion";

export default function StepProgress({ step, total }: { step: number; total: number }) {
  const pct = Math.max(0, Math.min(100, (step / total) * 100));
  return (
    <div data-testid="step-progress" className="fixed top-0 left-0 right-0 z-50 h-1 bg-[#27272A]/60">
      <motion.div
        className="h-full bg-gradient-to-r from-[#00F2FE] to-[#FF4F00]"
        style={{ boxShadow: "0 0 12px rgba(255,79,0,0.5)" }}
        initial={false}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      />
    </div>
  );
}
