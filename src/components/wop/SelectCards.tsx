import { motion } from "framer-motion";
import { Check } from "lucide-react";
import type { ReactNode } from "react";

export interface SelectOption {
  value: string;
  label: string;
  hint?: string;
  icon?: ReactNode;
}

interface Props {
  options: SelectOption[];
  value: string;
  onChange: (v: string) => void;
  testIdPrefix?: string;
  columns?: 2 | 3;
}

export default function SelectCards({ options, value, onChange, testIdPrefix = "card", columns = 2 }: Props) {
  const grid = columns === 3 ? "grid-cols-1 sm:grid-cols-3" : "grid-cols-1 sm:grid-cols-2";
  return (
    <div className={`grid gap-3 ${grid}`}>
      {options.map((opt) => {
        const selected = value === opt.value;
        const slug = opt.value.toLowerCase().replace(/[^a-z0-9]+/g, "-");
        return (
          <motion.button
            key={opt.value}
            type="button"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onChange(opt.value)}
            data-testid={`${testIdPrefix}-${slug}`}
            className={`group relative overflow-hidden text-left rounded-xl border px-5 py-4 transition-all duration-300 ${
              selected
                ? "border-whop-orange bg-[#FF4F00]/10 shadow-[0_0_24px_rgba(255,79,0,0.25)]"
                : "border-whop-border bg-whop-surface hover:border-[#FF4F00]/50 hover:bg-[#FF4F00]/5"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                {opt.icon && (
                  <span className={selected ? "text-whop-orange" : "text-whop-text"}>{opt.icon}</span>
                )}
                <div>
                  <div className="font-display text-base sm:text-lg font-medium text-white">{opt.label}</div>
                  {opt.hint && <div className="mt-0.5 text-xs text-whop-text">{opt.hint}</div>}
                </div>
              </div>
              <span
                className={`mt-0.5 flex h-5 w-5 items-center justify-center rounded-full border transition-all ${
                  selected ? "border-whop-orange bg-whop-orange text-white" : "border-whop-border text-transparent"
                }`}
              >
                <Check className="h-3 w-3" strokeWidth={3} />
              </span>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
}
