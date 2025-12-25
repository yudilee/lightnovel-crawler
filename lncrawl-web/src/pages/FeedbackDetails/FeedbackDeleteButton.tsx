import type { Feedback } from '@/types';
import { stringifyError } from '@/utils/errors';
import { DeleteOutlined } from '@ant-design/icons';
import { Button, message, Popconfirm } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const FeedbackDeleteButton: React.FC<{
  feedback: Feedback;
}> = ({ feedback }) => {
  const navigate = useNavigate();
  const [messageApi, contextHolder] = message.useMessage();

  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`/api/feedback/${feedback.id}`);
      messageApi.success('Feedback deleted successfully');
      navigate('/feedbacks');
    } catch (err) {
      messageApi.error(stringifyError(err, 'Failed to delete feedback'));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Popconfirm
        title="Delete feedback"
        description="Are you sure you want to permanently delete this feedback?"
        onConfirm={handleDelete}
        okText="Yes, delete"
        okType="danger"
        cancelText="Cancel"
      >
        <Button danger icon={<DeleteOutlined />} loading={deleting}>
          Delete
        </Button>
      </Popconfirm>
    </>
  );
};
