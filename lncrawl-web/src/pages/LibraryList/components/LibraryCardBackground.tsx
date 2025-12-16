import type React from 'react';
import { getGradientForId } from './utils/gradients';

type LibraryCardBackgroundProps = {
  libraryId: string;
  novelCount: number;
};

export const LibraryCardBackground: React.FC<LibraryCardBackgroundProps> = ({
  libraryId,
}) => {
  const gradientBackground = getGradientForId(libraryId);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 0,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          background: gradientBackground,
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            'linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.7) 100%)',
        }}
      />
    </div>
  );
};
