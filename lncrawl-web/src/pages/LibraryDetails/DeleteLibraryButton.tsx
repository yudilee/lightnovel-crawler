import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DeleteOutlined } from '@ant-design/icons';
import { Button, message, Modal } from 'antd';
import axios from 'axios';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface DeleteLibraryButtonProps {
  library: Library;
  disabled?: boolean;
}

export const DeleteLibraryButton: React.FC<DeleteLibraryButtonProps> = ({
  library,
  disabled,
}) => {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const handleDelete = () => {
    setIsModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await axios.delete(`/api/library/${library.id}`);
      messageApi.success('Library deleted successfully');
      navigate('/libraries');
    } catch (err) {
      messageApi.error(stringifyError(err));
      setIsDeleting(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Button
        danger
        icon={<DeleteOutlined />}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          handleDelete();
        }}
        loading={isDeleting}
        disabled={disabled || isDeleting}
      >
        Delete
      </Button>

      <Modal
        title="Delete Library"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleDeleteConfirm}
        cancelText="Cancel"
        okText="Delete"
        width={500}
      >
        <p>
          Are you sure you want to delete the library &quot;{library.name}
          &quot;?
        </p>
      </Modal>
    </>
  );
};
