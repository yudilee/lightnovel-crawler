import { Typography } from 'antd';
import type React from 'react';

type LibraryCardDescriptionProps = {
  description?: string;
};

export const LibraryCardDescription: React.FC<LibraryCardDescriptionProps> = ({
  description,
}) => {
  return (
    <Typography.Paragraph
      ellipsis={{ rows: 3 }}
      style={{
        color: 'rgba(255, 255, 255, 0.95)',
        marginBottom: 'auto',
        textShadow: '0 1px 2px rgba(0,0,0,0.5)',
        fontSize: 13,
        lineHeight: 1.6,
      }}
    >
      {description || 'No description available'}
    </Typography.Paragraph>
  );
};

