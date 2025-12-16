import type { Library } from '@/types';
import { Form, Input, Modal } from 'antd';
import React, { useEffect } from 'react';

interface EditLibraryModalProps {
  open: boolean;
  library: Library | undefined;
  onCancel: () => void;
  onSubmit: (values: { name: string; description: string }) => Promise<void>;
}

export const EditLibraryModal: React.FC<EditLibraryModalProps> = ({
  open,
  library,
  onCancel,
  onSubmit,
}) => {
  const [editForm] = Form.useForm();

  const handleOk = async () => {
    try {
      const values = await editForm.validateFields();
      await onSubmit(values);
      editForm.resetFields();
    } catch (err) {
      // Validation errors are handled by form
    }
  };

  const handleCancel = () => {
    editForm.resetFields();
    onCancel();
  };

  // Update form when library changes
  useEffect(() => {
    if (library && open) {
      editForm.setFieldsValue({
        name: library.name,
        description: library.description || '',
      });
    }
  }, [library, open, editForm]);

  return (
    <Modal
      title="Edit Library"
      open={open}
      onCancel={handleCancel}
      onOk={handleOk}
      okText="Save"
    >
      <Form
        form={editForm}
        layout="vertical"
        onFinish={onSubmit}
      >
        <Form.Item
          name="name"
          label="Library Name"
          rules={[{ required: true, message: 'Please enter a library name' }]}
        >
          <Input placeholder="Enter library name" />
        </Form.Item>
        <Form.Item
          name="description"
          label="Description"
        >
          <Input.TextArea
            placeholder="Enter library description (optional)"
            rows={4}
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

