import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { FolderAddOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Modal, Switch } from 'antd';
import axios from 'axios';
import { useState } from 'react';

type FormValues = {
  name: string;
  description?: string;
  is_public?: boolean;
};

export const CreateLibraryButton: React.FC<{
  onSuccess?: () => void;
}> = ({ onSuccess }) => {
  const [form] = Form.useForm<FormValues>();
  const [messageApi, contextHolder] = message.useMessage();

  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleCreate = async (values: FormValues) => {
    setSaving(true);
    try {
      await axios.post<Library>('/api/library', {
        name: values.name,
        description: values.description,
        is_public: Boolean(values.is_public),
      });
      messageApi.success('Library created successfully');
      form.resetFields();
      setOpen(false);
      onSuccess?.();
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Button
        type="primary"
        loading={saving}
        icon={<FolderAddOutlined />}
        onClick={() => setOpen(true)}
      >
        New Library
      </Button>

      <Modal
        title="Create library"
        open={open}
        onCancel={() => setOpen(false)}
        destroyOnHidden
        onOk={() => handleCreate(form.getFieldsValue())}
        okText="Save"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
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

          <Form.Item
            label="Make public"
            name="is_public"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
