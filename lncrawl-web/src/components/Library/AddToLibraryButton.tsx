import { PlusOutlined } from '@ant-design/icons';
import type { ButtonProps } from 'antd';
import { Button } from 'antd';
import { useState } from 'react';
import { AddToLibraryModal } from './AddToLibraryModal';

interface Props {
  novelId: string;
  buttonText?: string;
  buttonType?: ButtonProps['type'];
  size?: ButtonProps['size'];
}

export const AddToLibraryButton: React.FC<Props> = ({
  novelId,
  buttonText = 'Add to Library',
  buttonType = 'default',
  size = 'middle',
}) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        icon={<PlusOutlined />}
        type={buttonType}
        size={size}
        onClick={() => setOpen(true)}
      >
        {buttonText}
      </Button>

      <AddToLibraryModal
        novelId={novelId}
        open={open}
        onCancel={() => setOpen(false)}
      />
    </>
  );
};
