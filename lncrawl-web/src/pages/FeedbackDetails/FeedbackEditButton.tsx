import { FeedbackTypeLabels } from '@/components/Tags/FeedbackTypeTag';
import { type Feedback, FeedbackType } from '@/types';
import { stringifyError } from '@/utils/errors';
import { EditOutlined } from '@ant-design/icons';
import { Button, Form, Input, message, Modal, Select, Space } from 'antd';
import axios from 'axios';
import { useState } from 'react';

type FormValues = {
  type?: FeedbackType;
  subject?: string;
  message?: string;
};

export const FeedbackEditButton: React.FC<{
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
      if (values.type !== undefined) {
        payload.type = values.type;
      }
      if (values.subject) {
        payload.subject = values.subject;
      }
      if (values.subject) {
        payload.subject = values.subject;
      }
      if (values.message) {
        payload.message = values.message;
      }
      const { data } = await axios.put<Feedback>(
        `/api/feedback/${feedback.id}`,
        payload
      );
      messageApi.success('Feedback updated successfully');
      setOpen(false);
      form.resetFields();
      onSuccess?.(data);
    } catch (err) {
      messageApi.error(stringifyError(err, 'Failed to update feedback'));
    } finally {
      setUpdating(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Button
        icon={<EditOutlined />}
        onClick={() => {
          form.setFieldsValue({
            type: feedback.type,
            subject: feedback.subject,
            message: feedback.message,
          });
          setOpen(true);
        }}
      >
        Edit
      </Button>

      {/* User Edit Modal */}
      <Modal
        title="Edit Feedback"
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
            type: feedback.type,
            subject: feedback.subject,
            message: feedback.message,
          }}
          size="large"
          layout="vertical"
          labelCol={{ style: { padding: 0 } }}
        >
          <Form.Item
            name="type"
            label="Type"
            rules={[{ required: true, message: 'Please select a type' }]}
          >
            <Select
              options={Object.values(FeedbackType).map((value) => ({
                value,
                label: FeedbackTypeLabels[value],
              }))}
            />
          </Form.Item>

          <Form.Item
            name="subject"
            label="Subject"
            rules={[
              { required: true, message: 'Please enter a subject' },
              { max: 200, message: 'Subject must be less than 200 characters' },
            ]}
          >
            <Input placeholder="Brief description" maxLength={200} />
          </Form.Item>

          <Form.Item
            name="message"
            label="Message"
            rules={[
              { required: true, message: 'Please enter a message' },
              {
                max: 5000,
                message: 'Message must be less than 5000 characters',
              },
            ]}
          >
            <Input.TextArea
              rows={6}
              placeholder="Detailed message"
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
                Save
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
