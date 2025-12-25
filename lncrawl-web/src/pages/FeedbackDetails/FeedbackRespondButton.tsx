import type { Feedback } from '@/types';
import { FeedbackStatus } from '@/types';
import { stringifyError } from '@/utils/errors';
import { MessageOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Modal, Select, Space } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import { FeedbackStatusLabels } from '../FeedbackList/utils';

type FormValues = {
  status?: FeedbackStatus;
  admin_notes?: string;
};

export const FeedbackRespondButton: React.FC<{
  feedback: Feedback;
  onSuccess?: (feedback: Feedback) => void;
}> = ({ feedback, onSuccess }) => {
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();

  const [open, setOpen] = useState(false);
  const [updating, setUpdating] = useState(false);

  const handleEdit = async (values: FormValues) => {
    setUpdating(true);
    try {
      const payload: FormValues = {};
      if (values.status !== undefined) {
        payload.status = values.status;
      }
      if (values.admin_notes) {
        payload.admin_notes = values.admin_notes;
      }
      const { data } = await axios.post<Feedback>(
        `/api/feedback/${feedback.id}/respond`,
        payload
      );
      messageApi.success('Feedback responded successfully');
      setOpen(false);
      form.resetFields();
      onSuccess?.(data);
    } catch (err) {
      messageApi.error(stringifyError(err, 'Failed to respond to feedback'));
    } finally {
      setUpdating(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Button
        icon={<MessageOutlined />}
        onClick={() => {
          form.setFieldsValue({
            status: feedback.status,
            admin_notes: feedback.admin_notes || '',
          });
          setOpen(true);
        }}
      >
        Respond
      </Button>

      <Modal
        title="Respond to Feedback"
        open={open}
        onCancel={() => {
          setOpen(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          onFinish={handleEdit}
          initialValues={{
            status: feedback.status,
            admin_notes: feedback.admin_notes || '',
          }}
          size="large"
          layout="vertical"
          labelCol={{ style: { padding: 0 } }}
        >
          <Form.Item name="status" label="Status">
            <Select
              options={Object.values(FeedbackStatus).map((value) => ({
                value,
                label: FeedbackStatusLabels[value],
              }))}
            />
          </Form.Item>

          <Form.Item
            name="admin_notes"
            label="Admin Notes"
            rules={[
              {
                max: 5000,
                message: 'Notes must be less than 5000 characters',
              },
            ]}
          >
            <Input.TextArea
              rows={6}
              placeholder="Admin notes or response"
              maxLength={5000}
              showCount
            />
          </Form.Item>

          <Form.Item style={{ marginTop: '40px' }}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button
                onClick={() => {
                  setOpen(false);
                  form.resetFields();
                }}
                disabled={updating}
              >
                Cancel
              </Button>
              <Button type="primary" htmlType="submit" loading={updating}>
                Respond
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
