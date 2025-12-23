import { FeedbackType } from '@/types';
import { stringifyError } from '@/utils/errors';
import { CommentOutlined } from '@ant-design/icons';
import { Button, Flex, Form, Input, message, Modal, Select, Space } from 'antd';
import axios from 'axios';
import { useState } from 'react';

const { TextArea } = Input;

const feedbackTypeOptions = [
  { value: FeedbackType.GENERAL, label: 'General' },
  { value: FeedbackType.ISSUE, label: 'Report Issue' },
  { value: FeedbackType.FEATURE, label: 'Suggest Feature' },
];

export const FeedbackButton: React.FC<{
  onSubmit?: () => any;
}> = ({ onSubmit }) => {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  const handleSubmit = async (values: {
    type: FeedbackType;
    subject: string;
    message: string;
  }) => {
    setLoading(true);
    try {
      await axios.post('/api/feedback', values);
      messageApi.success('Feedback submitted successfully! Thank you.');
      form.resetFields();
      setOpen(false);
      onSubmit?.();
    } catch (err) {
      messageApi.error(stringifyError(err, 'Failed to submit feedback'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {contextHolder}

      <Button
        type="primary"
        icon={<CommentOutlined />}
        onClick={() => setOpen(true)}
      >
        Submit Feedback
      </Button>

      <Modal
        title={
          <Space>
            <CommentOutlined /> Submit Feedback
          </Space>
        }
        open={open}
        onCancel={() => setOpen(false)}
        footer={null}
        width={600}
        destroyOnHidden
      >
        <Form
          form={form}
          size="large"
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          labelCol={{ style: { padding: 0 } }}
        >
          <Form.Item
            name="type"
            label="Feedback Type"
            initialValue={FeedbackType.GENERAL}
            rules={[
              { required: true, message: 'Please select a feedback type' },
            ]}
          >
            <Select
              placeholder="Select feedback type"
              options={feedbackTypeOptions}
            />
          </Form.Item>

          <Form.Item
            name="subject"
            label="Subject"
            rules={[
              { required: true, message: 'Please enter a subject' },
              { max: 100, message: 'Subject must be less than 100 characters' },
            ]}
          >
            <Input
              placeholder="Brief description of your feedback"
              maxLength={100}
              showCount
            />
          </Form.Item>

          <Form.Item
            name="message"
            label="Message"
            rules={[
              { required: true, message: 'Please enter a message' },
              {
                max: 1000,
                message: 'Message must be less than 1000 characters',
              },
            ]}
          >
            <TextArea
              placeholder="Please provide detailed information about your feedback..."
              rows={6}
              maxLength={1000}
              showCount
            />
          </Form.Item>

          <Form.Item style={{ marginTop: 35 }}>
            <Flex justify="end" gap={10}>
              <Button onClick={() => setOpen(false)} disabled={loading}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                Submit
              </Button>
            </Flex>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
