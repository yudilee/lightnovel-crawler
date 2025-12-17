import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { FolderAddOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreateLibraryModal } from '../LibraryList/CreateLibraryModal';

export const CreateLibraryButton: React.FC<any> = () => {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();

  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const handleCreate = async (values: {
    name: string;
    description?: string;
    is_public?: boolean;
  }) => {
    setCreating(true);
    try {
      const { data } = await axios.post<Library>('/api/library', {
        name: values.name,
        description: values.description,
        is_public: Boolean(values.is_public),
      });
      messageApi.success('Library created successfully');
      navigate(`/library/${data.id}`);
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setCreating(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Button
        icon={<FolderAddOutlined />}
        type="primary"
        onClick={() => setCreateOpen(true)}
      >
        New Library
      </Button>
      <CreateLibraryModal
        open={createOpen}
        loading={creating}
        onSubmit={handleCreate}
        onCancel={() => setCreateOpen(false)}
      />
    </>
  );
};
