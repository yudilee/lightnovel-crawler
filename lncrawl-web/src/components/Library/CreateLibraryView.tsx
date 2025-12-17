import type { Library } from '@/types';
import { stringifyError } from '@/utils/errors';
import { ArrowLeftOutlined } from '@ant-design/icons';
import {
  Button,
  Flex,
  Form,
  Input,
  Space,
  Switch,
  Typography,
  message,
} from 'antd';
import axios from 'axios';
import { useState } from 'react';

interface FormValues {
  name: string;
  description?: string;
  is_public?: boolean;
}

interface Props {
  novelId: string;
  onBack: () => void;
  onSuccess: () => void;
}

export const CreateLibraryView: React.FC<Props> = ({
  novelId,
  onBack,
  onSuccess,
}) => {
  const [form] = Form.useForm<FormValues>();
  const [saving, setSaving] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  const handleSubmit = async (values: FormValues) => {
    if (!values.name?.trim()) {
      messageApi.error('Library name is required');
      return;
    }

    setSaving(true);
    try {
      const { data } = await axios.post<Library>('/api/library', {
        name: values.name.trim(),
        description: values.description?.trim(),
        is_public: Boolean(values.is_public),
      });
      await axios.put(`/api/library/${data.id}/novel/${novelId}`);
      messageApi.success('Novel added to library successfully');
      onSuccess();
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Form<FormValues>
        form={form}
        size="large"
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{ is_public: false }}
        labelCol={{ style: { padding: 0 } }}
      >
        <Form.Item
          label="Name"
          name="name"
          rules={[{ required: true, message: 'Library name is required' }]}
        >
          <Input placeholder="My favorite novels" />
        </Form.Item>

        <Form.Item label="Description" name="description">
          <Input.TextArea placeholder="Optional description" rows={3} />
        </Form.Item>

        <Form.Item label="Visibility" name="is_public" valuePropName="checked">
          <Space>
            <Switch />
            <Typography.Text>Visible to everyone</Typography.Text>
          </Space>
        </Form.Item>

        <Form.Item>
          <Flex gap={8} justify="flex-end">
            <Button icon={<ArrowLeftOutlined />} onClick={onBack}>
              Back
            </Button>
            <Button type="primary" htmlType="submit" loading={saving}>
              Create & Add
            </Button>
          </Flex>
        </Form.Item>
      </Form>
    </>
  );
};
