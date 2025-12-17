import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { EditOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Modal } from 'antd';
import axios from 'axios';
import React, { useState } from 'react';

interface FormValues {
  name: string;
  description: string;
}

export const EditLibraryButton: React.FC<{
  library: Library;
  disabled?: boolean;
}> = ({ library, disabled }) => {
  const [form] = Form.useForm<FormValues>();
  const [messageApi, contextHolder] = message.useMessage();
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleEdit = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsModalOpen(true);
  };

  const handleEditSubmit = async (values: FormValues) => {
    if (!library.id) return;
    setIsSubmitting(true);
    try {
      await axios.patch(`/api/library/${library.id}`, {
        name: values.name,
        description: values.description || undefined,
      });
      messageApi.success('Library updated successfully');
      setIsModalOpen(false);
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

      <Modal
        title="Edit Library"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => handleEditSubmit(form.getFieldsValue())}
        okText="Save"
      >
        <Form<FormValues>
          form={form}
          layout="vertical"
          onFinish={handleEditSubmit}
          initialValues={{
            name: library.name,
            description: library.description || '',
          }}
        >
          <Form.Item
            name="name"
            label="Library Name"
            rules={[{ required: true, message: 'Library name is required' }]}
          >
            <Input placeholder="My Favorite Novels" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea
              placeholder="Library description (optional)"
              rows={4}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
