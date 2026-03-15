import React from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

type TiltMotionCardProps = React.ComponentProps<typeof motion.div> & {
  tiltStrength?: number;
};

const TiltMotionCard: React.FC<TiltMotionCardProps> = ({ tiltStrength = 8, style, onMouseMove, onMouseLeave, ...props }) => {
  const rotateXTarget = useMotionValue(0);
  const rotateYTarget = useMotionValue(0);
  const rotateX = useSpring(rotateXTarget, { stiffness: 260, damping: 28, mass: 0.6 });
  const rotateY = useSpring(rotateYTarget, { stiffness: 260, damping: 28, mass: 0.6 });

  return (
    <motion.div
      {...props}
      style={{
        ...style,
        rotateX,
        rotateY,
        transformPerspective: 1100,
        transformStyle: 'preserve-3d',
        willChange: 'transform',
      }}
      onMouseMove={(event) => {
        const bounds = event.currentTarget.getBoundingClientRect();
        const relativeX = (event.clientX - bounds.left) / bounds.width;
        const relativeY = (event.clientY - bounds.top) / bounds.height;
        const centeredX = relativeX - 0.5;
        const centeredY = relativeY - 0.5;

        rotateXTarget.set(-centeredY * tiltStrength);
        rotateYTarget.set(centeredX * tiltStrength);

        if (onMouseMove) {
          onMouseMove(event);
        }
      }}
      onMouseLeave={(event) => {
        rotateXTarget.set(0);
        rotateYTarget.set(0);
        if (onMouseLeave) {
          onMouseLeave(event);
        }
      }}
    />
  );
};

export default TiltMotionCard;
