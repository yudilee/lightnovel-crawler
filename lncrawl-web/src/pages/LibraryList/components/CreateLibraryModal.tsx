import { Form, Input, Modal, Switch } from 'antd';
import type React from 'react';

type FormValues = {
  name: string;
  description?: string;
  is_public?: boolean;
};

type CreateLibraryModalProps = {
  open: boolean;
  loading?: boolean;
  onSubmit: (values: FormValues) => void;
  onCancel: () => void;
};

export const CreateLibraryModal: React.FC<CreateLibraryModalProps> = ({
  open,
  loading,
  onSubmit,
  onCancel,
}) => (
  <Modal
    title="Create library"
    open={open}
    onCancel={onCancel}
    okButtonProps={{
      loading,
      htmlType: 'submit',
      form: 'create-library-form',
    }}
    destroyOnHidden
  >
    <Form
      id="create-library-form"
      layout="vertical"
      onFinish={onSubmit}
      initialValues={{ is_public: false }}
    >
      <Form.Item
        label="Name"
        name="name"
        rules={[{ required: true, message: 'Name is required' }]}
      >
        <Input placeholder="My library" />
      </Form.Item>
      <Form.Item label="Description" name="description">
        <Input.TextArea rows={3} placeholder="Optional description" />
      </Form.Item>
      <Form.Item label="Make public" name="is_public" valuePropName="checked">
        <Switch />
      </Form.Item>
    </Form>
  </Modal>
);
