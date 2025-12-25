import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DeleteOutlined } from '@ant-design/icons';
import { Button, message, Popconfirm } from 'antd';
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
  const [deleting, setDeleting] = useState<boolean>(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`/api/library/${library.id}`);
      messageApi.success('Library deleted successfully');
      navigate('/libraries');
    } catch (err) {
      messageApi.error(stringifyError(err));
      setDeleting(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Popconfirm
        title="Delete library"
        description="Are you sure you want to permanently delete this library?"
        onConfirm={handleDelete}
        okText="Yes, delete"
        okType="danger"
        cancelText="Cancel"
      >
        <Button
          danger
          icon={<DeleteOutlined />}
          loading={deleting}
          disabled={disabled || deleting}
        >
          Delete
        </Button>
      </Popconfirm>
    </>
  );
};
