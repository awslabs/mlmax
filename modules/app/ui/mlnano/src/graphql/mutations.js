/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createDataSet = /* GraphQL */ `
  mutation CreateDataSet(
    $input: CreateDataSetInput!
    $condition: ModelDataSetConditionInput
  ) {
    createDataSet(input: $input, condition: $condition) {
      id
      name
      description
      file {
        bucket
        region
        key
      }
      createdAt
      updatedAt
    }
  }
`;
export const updateDataSet = /* GraphQL */ `
  mutation UpdateDataSet(
    $input: UpdateDataSetInput!
    $condition: ModelDataSetConditionInput
  ) {
    updateDataSet(input: $input, condition: $condition) {
      id
      name
      description
      file {
        bucket
        region
        key
      }
      createdAt
      updatedAt
    }
  }
`;
export const deleteDataSet = /* GraphQL */ `
  mutation DeleteDataSet(
    $input: DeleteDataSetInput!
    $condition: ModelDataSetConditionInput
  ) {
    deleteDataSet(input: $input, condition: $condition) {
      id
      name
      description
      file {
        bucket
        region
        key
      }
      createdAt
      updatedAt
    }
  }
`;
