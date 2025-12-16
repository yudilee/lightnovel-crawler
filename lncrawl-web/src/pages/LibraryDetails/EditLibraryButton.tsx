import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { EditOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import axios from 'axios';
import React, { useState } from 'react';
import { EditLibraryModal } from './EditLibraryModal';

interface EditLibraryButtonProps {
  library: Library;
  onSuccess?: (updatedLibrary: Library) => void;
  disabled?: boolean;
}

export const EditLibraryButton: React.FC<EditLibraryButtonProps> = ({
  library,
  onSuccess,
  disabled,
}) => {
  const [messageApi, contextHolder] = message.useMessage();
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleEdit = () => {
    setIsModalOpen(true);
  };

  const handleEditSubmit = async (values: {
    name: string;
    description: string;
  }) => {
    if (!library.id) return;
    setIsSubmitting(true);
    try {
      const { data } = await axios.patch<Library>(
        `/api/library/${library.id}`,
        {
          name: values.name,
          description: values.description || undefined,
        }
      );
      messageApi.success('Library updated successfully');
      setIsModalOpen(false);
      onSuccess?.(data);
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Button
        icon={<EditOutlined />}
        onClick={handleEdit}
        disabled={disabled || isSubmitting}
      >
        Edit
      </Button>
      <EditLibraryModal
        open={isModalOpen}
        library={library}
        onCancel={() => setIsModalOpen(false)}
        onSubmit={handleEditSubmit}
      />
    </>
  );
};
